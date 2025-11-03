    <template>
    <h1>Login</h1>
    <div id='container'>
        <form id='form-container'>
            <label>Email</label>
        <input type='email' placeholder='Email'>
        
        <label>Senha</label>
        <input type='password' placeholder='Senha'>
        
        <button type='button'>Entrar</button> 
        </form>
    </div>
    </template>

    <script setup>

    </script>

    <style scoped>
    div{
        display:flex;
        flex-direction: column;
        align-items: center;
    }
    form{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    </style>